import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_excel(BASE_DIR / "analysis_dataset.xlsx")

unique_players = (
	df[["Player"]]
	.drop_duplicates()
	.sort_values("Player")
	.reset_index(drop=True)
)

unique_players.to_excel(
	BASE_DIR / "unique_players.xlsx",
	index=False
)

print("="*40)
print("Unique players created!")
print("="*40)
print(f"Unique players: {len(unique_players)}")
