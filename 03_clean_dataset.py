from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "SuperLiga_2021_2026.xlsx"
OUTPUT_FILE = BASE_DIR / "SuperLiga_2021_2026_clean.xlsx"


df = pd.read_excel(INPUT_FILE)

print("=" * 60)
print("VERIFICAREA COLOANELOR SIMILARE")
print("=" * 60)

pairs = [
    ("Pase lungi per 90", "Pase lungi per 90.1"),
    ("Acuratețea paselor lungi, %", "Acuratețe pase lungi, %")
]

for col1, col2 in pairs:

    if col1 in df.columns and col2 in df.columns:

        identical = df[col1].equals(df[col2])

        print(f"\n{col1}")
        print(f"{col2}")

        if identical:
            print("→ Coloanele sunt IDENTICE.")
            df.drop(columns=[col2], inplace=True)
            print(f"→ {col2} a fost eliminată.")

        else:
            differences = (df[col1] != df[col2]).sum()

            print("→ Coloanele NU sunt identice.")
            print(f"→ Număr valori diferite: {differences}")

print("\nElimin spațiile inutile din textele existente...")

text_columns = df.select_dtypes(include="object").columns

for column in text_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .replace("nan", pd.NA)
    )

df.to_excel(OUTPUT_FILE, index=False)

print("\n" + "=" * 60)
print("DATASET CURĂȚAT")
print("=" * 60)

print(f"Număr coloane final: {len(df.columns)}")
print(f"Fișier salvat:\n{OUTPUT_FILE}")
