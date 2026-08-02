import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_excel(BASE_DIR / "SuperLiga_2021_2026.xlsx")

# Selectăm coloanele utile
players = df[[
    "Player",
    "Season",
    "Team",
    "Age",
    "Minutes played"
]]

# Eliminăm duplicatele
players = players.drop_duplicates()

# Sortăm pentru verificare ușoară
players = players.sort_values(
    ["Season", "Team", "Player"]
).reset_index(drop=True)

players.to_excel(
    BASE_DIR / "transfer_candidates.xlsx",
    index=False
)

print(players.head())
print()
print(f"Rows: {len(players)}")
