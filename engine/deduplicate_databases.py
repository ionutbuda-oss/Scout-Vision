from pathlib import Path
import pandas as pd
import re

DATABASE_DIR = Path("databases")
OUTPUT_DIR = Path("outputs/global_database")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "scoutvision_global_unique.xlsx"


def normalize_name(value):
    if pd.isna(value):
        return ""
    value = str(value).strip().casefold()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_position(value):
    if pd.isna(value):
        return ""
    return str(value).strip().casefold()


frames = []

for path in sorted(DATABASE_DIR.glob("*.xlsx")):

    try:
        xls = pd.ExcelFile(path)

        selected = None

        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            df.columns = df.columns.astype(str).str.strip()

            if "Player" in df.columns:
                selected = df
                break

        if selected is None:
            continue

        df = selected.copy()

        df["Source Database"] = path.name

        df["_Player Key"] = df["Player"].apply(normalize_name)

        if "Age" in df.columns:
            df["_Age Key"] = pd.to_numeric(
                df["Age"],
                errors="coerce"
            )
        else:
            df["_Age Key"] = pd.NA

        df["_Position Key"] = (
            df["Position"].apply(normalize_position)
            if "Position" in df.columns
            else ""
        )

        frames.append(df)

    except Exception as e:
        print(f"ERROR: {path.name} -> {e}")


if not frames:
    raise RuntimeError("No usable databases found.")

all_players = pd.concat(
    frames,
    ignore_index=True,
    sort=False,
)

print("=" * 110)
print("SCOUTVISION — GLOBAL DATABASE DEDUPLICATION")
print("=" * 110)

print(f"Original rows: {len(all_players)}")

# ------------------------------------------------------------
# DUPLICATE GROUPS
# ------------------------------------------------------------

identity_keys = [
    "_Player Key",
    "_Age Key",
    "_Position Key",
]

all_players["_Identity Key"] = (
    all_players["_Player Key"].astype(str)
    + "|"
    + all_players["_Age Key"].astype(str)
    + "|"
    + all_players["_Position Key"].astype(str)
)

group_sizes = (
    all_players
    .groupby("_Identity Key")
    .size()
)

duplicate_keys = group_sizes[
    group_sizes > 1
].index

duplicate_rows = all_players[
    all_players["_Identity Key"].isin(duplicate_keys)
].copy()

# ------------------------------------------------------------
# SAFE DEDUPLICATION
# ------------------------------------------------------------

# Exact identity match:
# same normalized player + same age + same position.
#
# We retain the first source and record all source databases.

unique_rows = []
review_rows = []

for key, group in all_players.groupby("_Identity Key"):

    group = group.copy()

    if len(group) == 1:

        unique_rows.append(
            group.iloc[0]
        )
        continue

    # Same identity signature.
    # If team names are identical, this is a very strong duplicate.
    teams = set()

    if "Team" in group.columns:
        teams = {
            str(x).strip().casefold()
            for x in group["Team"]
            if pd.notna(x)
        }

    # Same player + age + position + same team
    if len(teams) <= 1:

        row = group.iloc[0].copy()

        row["Duplicate Sources"] = " | ".join(
            sorted(
                set(
                    group["Source Database"]
                    .astype(str)
                )
            )
        )

        row["Duplicate Count"] = len(group)

        unique_rows.append(row)

    else:

        # Different teams = potentially same player transferred
        # OR genuine homonym.
        #
        # Do NOT silently delete.
        review_rows.append(group)

# ------------------------------------------------------------
# BUILD OUTPUTS
# ------------------------------------------------------------

unique_df = pd.DataFrame(unique_rows)

if review_rows:
    review_df = pd.concat(
        review_rows,
        ignore_index=True,
        sort=False,
    )
else:
    review_df = pd.DataFrame()

# Remove technical columns
technical = [
    "_Player Key",
    "_Age Key",
    "_Position Key",
    "_Identity Key",
]

unique_df = unique_df.drop(
    columns=[
        c for c in technical
        if c in unique_df.columns
    ],
    errors="ignore",
)

review_df = review_df.drop(
    columns=[
        c for c in technical
        if c in review_df.columns
    ],
    errors="ignore",
)

# ------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl",
) as writer:

    unique_df.to_excel(
        writer,
        sheet_name="Global Unique",
        index=False,
    )

    if not review_df.empty:
        review_df.to_excel(
            writer,
            sheet_name="REVIEW",
            index=False,
        )

    duplicate_rows.drop(
        columns=[
            c for c in technical
            if c in duplicate_rows.columns
        ],
        errors="ignore",
    ).to_excel(
        writer,
        sheet_name="Duplicate Groups",
        index=False,
    )

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print()
print("=" * 110)
print("SCOUTVISION — DEDUPLICATION SUMMARY")
print("=" * 110)

print(f"Original rows:              {len(all_players)}")
print(f"Unique rows:                {len(unique_df)}")
print(f"Rows removed automatically: {len(all_players) - len(unique_df)}")
print(f"Review rows:                {len(review_df)}")
print(f"Duplicate groups:           {len(duplicate_keys)}")

print()
print(f"Output: {OUTPUT_FILE}")

if not review_df.empty:
    print()
    print("⚠️ IMPORTANT")
    print(
        "Cases with same Player + Age + Position but different teams "
        "were NOT deleted. They are in the REVIEW sheet."
    )

print()
print("✅ GLOBAL DATABASE CREATED")
