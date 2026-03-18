"""
Phase 2 – Run all SQL analysis queries and export results to CSV.
Reads queries from: sql/queries.sql
Outputs CSVs to:    data/sql_results/
"""

import sqlite3
import pandas as pd
import re
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent
DB     = BASE / "data" / "superstore.db"
SQL    = BASE / "sql" / "queries.sql"
OUT    = BASE / "data" / "sql_results"
OUT.mkdir(exist_ok=True)

# ── Parse individual queries from the .sql file ──────────────
raw = SQL.read_text(encoding="utf-8")

# Split on the section-header comments (lines starting with "-- --")
blocks = re.split(r"--\s*──[^─]*──+", raw)

# Map each block to a short filename
query_names = [
    "01_revenue_by_month",
    "02_revenue_by_category",
    "03_revenue_by_subcategory",
    "04_revenue_by_region",
    "05_top10_products",
    "06_bottom10_products",
    "07_revenue_by_segment",
    "08_quarterly_growth",
    "09_profit_flag_summary",
    "10_top5_states",
]

conn = sqlite3.connect(DB)

for name, block in zip(query_names, blocks[1:]):   # blocks[0] is the file header
    sql_text = block.strip()
    if not sql_text:
        continue

    # Keep only the SELECT statement (drop leading comment lines)
    lines = [l for l in sql_text.splitlines() if not l.strip().startswith("--")]
    sql_text = "\n".join(lines).strip()

    df = pd.read_sql_query(sql_text, conn)
    out_path = OUT / f"{name}.csv"
    df.to_csv(out_path, index=False)
    print(f"  {name}: {len(df)} rows  ->  {out_path.name}")

conn.close()

# ── Quick summary print ───────────────────────────────────────
print("\n=== KEY FINDINGS ===")

revenue_by_cat = pd.read_csv(OUT / "02_revenue_by_category.csv")
print("\nRevenue & Profit by Category:")
print(revenue_by_cat.to_string(index=False))

region = pd.read_csv(OUT / "04_revenue_by_region.csv")
print("\nRevenue by Region:")
print(region.to_string(index=False))

top_products = pd.read_csv(OUT / "05_top10_products.csv")
print("\nTop 5 Products by Revenue:")
print(top_products.head(5).to_string(index=False))

loss_products = pd.read_csv(OUT / "06_bottom10_products.csv")
print("\nBottom 5 Products by Profit:")
print(loss_products.head(5).to_string(index=False))

print("\nAll results saved to data/sql_results/")
