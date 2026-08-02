
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Load analysis dataset
df = pd.read_excel(BASE_DIR / "analysis_dataset.xlsx")

# Keep only required columns
transfer_template = df[
	[
		"Player",
		"Season",
		"Age",
		"Minutes played"
	]
].copy()

# Remove duplicates
transfer_template = transfer_template.drop_duplicates()

# Sort
transfer_template = transfer_template.sort_values(
	["Season", "Player"]
).reset_index(drop=True)

# Save
transfer_template.to_excel(
	BASE_DIR / "transfer_template.xlsx",
	index=False
)

print("="*40)
print("Transfer template created!")
print("="*40)
print(f"Rows: {len(transfer_template)}")
