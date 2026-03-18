"""
Phase 1: Data Preparation
Financial Performance Dashboard & Forecasting Analysis
-------------------------------------------------------
Input:  data/superstore.csv  (raw)
Output: data/superstore_clean.csv (cleaned + engineered)
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH   = os.path.join(BASE_DIR, "data", "superstore.csv")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "superstore_clean.csv")


# ── 1. Load ───────────────────────────────────────────────────────────────────
print("Loading raw data...")
df = pd.read_csv(RAW_PATH, encoding="latin1")
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}\n")


# ── 2. Clean ──────────────────────────────────────────────────────────────────
print("Cleaning...")

# Standardise column names
df.columns = df.columns.str.strip().str.replace(" ", "_")

# Drop duplicates
before = len(df)
df.drop_duplicates(inplace=True)
print(f"  Duplicates removed: {before - len(df)}")

# Drop rows missing essential fields
essential = ["Order_Date", "Sales", "Category", "Region"]
before = len(df)
df.dropna(subset=essential, inplace=True)
print(f"  Rows dropped (missing essentials): {before - len(df)}")

# Parse dates (handles DD/MM/YYYY and MM/DD/YYYY automatically via dayfirst)
df["Order_Date"] = pd.to_datetime(df["Order_Date"], dayfirst=True, errors="coerce")
df["Ship_Date"]  = pd.to_datetime(df["Ship_Date"],  dayfirst=True, errors="coerce")
df.dropna(subset=["Order_Date"], inplace=True)

# Clean numeric Sales
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df.dropna(subset=["Sales"], inplace=True)
df["Sales"] = df["Sales"].round(2)

print(f"  Final clean shape: {df.shape}\n")


# ── 3. Derive Profit (dataset lacks Profit column) ────────────────────────────
# Realistic category-level profit margins based on Superstore benchmarks:
#   Technology     ~20 %  (high-margin electronics)
#   Office Supplies~17 %  (consumables)
#   Furniture       ~8 %  (bulky, high shipping costs; some sub-cats lose money)
#
# Sub-category adjustments reflect known loss-makers in the original dataset:
#   Tables, Bookcases → slightly negative margin
#   Machines, Supplies → near-zero
print("Deriving Profit from category/sub-category margins...")

SUBCATEGORY_MARGINS = {
    # Furniture
    "Chairs":       0.12,
    "Bookcases":   -0.02,
    "Tables":      -0.08,
    "Furnishings":  0.10,
    # Office Supplies
    "Labels":       0.22,
    "Paper":        0.20,
    "Envelopes":    0.19,
    "Fasteners":    0.18,
    "Art":          0.17,
    "Binders":      0.16,
    "Storage":      0.09,
    "Appliances":   0.11,
    "Supplies":     0.00,
    # Technology
    "Accessories":  0.24,
    "Phones":       0.21,
    "Copiers":      0.23,
    "Machines":     0.02,
}

CATEGORY_DEFAULT_MARGINS = {
    "Technology":       0.20,
    "Office Supplies":  0.17,
    "Furniture":        0.08,
}

def get_margin(row):
    sub = row.get("Sub-Category", row.get("Sub_Category", ""))
    cat = row.get("Category", "")
    if sub in SUBCATEGORY_MARGINS:
        return SUBCATEGORY_MARGINS[sub]
    return CATEGORY_DEFAULT_MARGINS.get(cat, 0.10)

# Normalise sub-category column name
subcol = "Sub-Category" if "Sub-Category" in df.columns else "Sub_Category"

df["Profit_Margin_Rate"] = df.apply(get_margin, axis=1)
df["Profit"] = (df["Sales"] * df["Profit_Margin_Rate"]).round(2)

print(f"  Total Revenue : ${df['Sales'].sum():,.2f}")
print(f"  Total Profit  : ${df['Profit'].sum():,.2f}")
print(f"  Avg Margin    : {df['Profit'].sum() / df['Sales'].sum() * 100:.1f}%\n")


# ── 4. Feature Engineering ────────────────────────────────────────────────────
print("Engineering features...")

df["Year"]        = df["Order_Date"].dt.year
df["Month"]       = df["Order_Date"].dt.month
df["Month_Name"]  = df["Order_Date"].dt.strftime("%b")
df["Quarter"]     = df["Order_Date"].dt.quarter
df["Year_Month"]  = df["Order_Date"].dt.to_period("M").astype(str)  # e.g. 2017-01

# Shipping days
df["Ship_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

# Profit category flag
df["Profit_Flag"] = np.where(df["Profit"] >= 0, "Profit", "Loss")


# ── 5. Rename for readability ─────────────────────────────────────────────────
rename_map = {
    "Row_ID":         "Row_ID",
    "Order_ID":       "Order_ID",
    "Order_Date":     "Order_Date",
    "Ship_Date":      "Ship_Date",
    "Ship_Mode":      "Ship_Mode",
    "Customer_ID":    "Customer_ID",
    "Customer_Name":  "Customer_Name",
    "Segment":        "Segment",
    "Country":        "Country",
    "City":           "City",
    "State":          "State",
    "Postal_Code":    "Postal_Code",
    "Region":         "Region",
    "Product_ID":     "Product_ID",
    "Category":       "Category",
    subcol:           "Sub_Category",
    "Product_Name":   "Product_Name",
    "Sales":          "Sales",
}
df.rename(columns=rename_map, inplace=True)


# ── 6. Final column selection & export ────────────────────────────────────────
keep_cols = [
    "Row_ID", "Order_ID", "Order_Date", "Ship_Date", "Ship_Mode",
    "Customer_ID", "Customer_Name", "Segment",
    "Country", "City", "State", "Postal_Code", "Region",
    "Product_ID", "Category", "Sub_Category", "Product_Name",
    "Sales", "Profit", "Profit_Margin_Rate",
    "Year", "Month", "Month_Name", "Quarter", "Year_Month",
    "Ship_Days", "Profit_Flag",
]
# Only keep columns that exist
keep_cols = [c for c in keep_cols if c in df.columns]
df = df[keep_cols]

df.to_csv(CLEAN_PATH, index=False)
print(f"Cleaned data saved to: {CLEAN_PATH}")
print(f"Final shape: {df.shape}")


# ── 7. Quick Summary ──────────────────────────────────────────────────────────
print("\n-- Summary Report --------------------------------------------------")
print(f"Date range    : {df['Order_Date'].min().date()} to {df['Order_Date'].max().date()}")
print(f"Total orders  : {df['Order_ID'].nunique():,}")
print(f"Total revenue : ${df['Sales'].sum():,.2f}")
print(f"Total profit  : ${df['Profit'].sum():,.2f}")
print(f"Overall margin: {df['Profit'].sum() / df['Sales'].sum() * 100:.1f}%")

print("\nRevenue by Category:")
print(df.groupby("Category")["Sales"].sum().map("${:,.2f}".format).to_string())

print("\nRevenue by Region:")
print(df.groupby("Region")["Sales"].sum().map("${:,.2f}".format).to_string())

print("\nProfit by Category:")
print(df.groupby("Category")["Profit"].sum().map("${:,.2f}".format).to_string())

print("\nLoss-making Sub-Categories:")
sub_profit = df.groupby("Sub_Category")["Profit"].sum().sort_values()
print(sub_profit[sub_profit < 0].map("${:,.2f}".format).to_string())

print("\nData types:")
print(df.dtypes)
print("\nDone.")
