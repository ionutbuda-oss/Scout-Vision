from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

FILES = [
    "2021-2022.xlsx",
    "2022-2023.xlsx",
    "2023-2024.xlsx",
    "2024-2025.xlsx",
    "2025-2026.xlsx",
]

all_data = []

reference_columns = None

for file in FILES:

    season = file.replace(".xlsx", "")

    print(f"Reading {season}...")

    df = pd.read_excel(BASE_DIR / file)

    df.columns = df.columns.str.strip()

    df.insert(0, "Season", season)

    if reference_columns is None:
        reference_columns = list(df.columns)

    else:
        if list(df.columns) != reference_columns:
            print(f"\nWARNING! Different columns in {season}\n")

    all_data.append(df)

dataset = pd.concat(all_data, ignore_index=True)

dataset.to_excel(
    BASE_DIR / "SuperLiga_2021_2026.xlsx",
    index=False
)

print("\n===================================")
print("Dataset created successfully!")
print("===================================")

print(f"Rows : {len(dataset)}")
print(f"Columns : {len(dataset.columns)}")
