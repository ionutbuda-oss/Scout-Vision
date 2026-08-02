import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Citire bază principală
df = pd.read_excel(BASE_DIR / "SuperLiga_2021_2026.xlsx")

# Filtrare după minute
analysis = df[df["Minutes played"] > 900].copy()

# Sortare
analysis = analysis.sort_values(
    ["Season", "Player"]
).reset_index(drop=True)

# Salvare
analysis.to_excel(
    BASE_DIR / "analysis_dataset.xlsx",
    index=False
)

print("=" * 40)
print("Analysis dataset created successfully!")
print("=" * 40)

print(f"Original dataset : {len(df)} rows")
print(f"Analysis dataset : {len(analysis)} rows")
print(f"Players removed  : {len(df)-len(analysis)}")
