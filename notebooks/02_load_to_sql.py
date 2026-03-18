"""
Phase 2 – Load cleaned Superstore data into SQLite database.
Creates: data/superstore.db  (table: sales)
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

df = pd.read_csv(DATA / "superstore_clean.csv", encoding="latin1", parse_dates=["Order_Date", "Ship_Date"])

conn = sqlite3.connect(DATA / "superstore.db")
df.to_sql("sales", conn, if_exists="replace", index=False)
conn.close()

print(f"Loaded {len(df):,} rows into superstore.db  ->  table: sales")
print("Columns:", df.columns.tolist())
