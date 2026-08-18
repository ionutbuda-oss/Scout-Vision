from pathlib import Path
import pandas as pd

DATABASE_DIR = Path("databases")
OUTPUT_DIR = Path("outputs/database_audit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_COLUMNS = [
    "Player",
    "Team",
    "Age",
    "Position",
    "Matches played",
    "Minutes played",
]

files = sorted(DATABASE_DIR.glob("*.xlsx"))

print("=" * 110)
print("SCOUTVISION — DATABASE AUDIT")
print("=" * 110)
print(f"Databases found: {len(files)}")
print()

audit = []
players_global = []

for path in files:

    try:
        xls = pd.ExcelFile(path)
        sheets = xls.sheet_names

        # Prima foaie care conține Player
        df = None
        selected_sheet = None

        for sheet in sheets:
            temp = pd.read_excel(path, sheet_name=sheet)
            temp.columns = temp.columns.astype(str).str.strip()

            if "Player" in temp.columns:
                df = temp
                selected_sheet = sheet
                break

        if df is None:
            audit.append({
                "Database": path.name,
                "Status": "ERROR — Player column missing",
                "Sheet": "",
                "Players": 0,
                "Columns": 0,
                "Missing Required": ", ".join(REQUIRED_COLUMNS),
                "Positions": "",
            })
            continue

        missing = [
            c for c in REQUIRED_COLUMNS
            if c not in df.columns
        ]

        players = (
            df["Player"]
            .astype(str)
            .str.strip()
        )

        players = players[
            (players != "") &
            (players.str.lower() != "nan")
        ]

        positions = ""

        if "Position" in df.columns:
            pos = (
                df["Position"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            position_counts = pos.value_counts()

            positions = " | ".join(
                f"{p}: {n}"
                for p, n in position_counts.items()
            )

        # Global player registry
        for player in players:
            players_global.append({
                "Player": player,
                "Database": path.name,
            })

        status = "READY" if not missing else "WARNING"

        audit.append({
            "Database": path.name,
            "Status": status,
            "Sheet": selected_sheet,
            "Players": len(players),
            "Columns": len(df.columns),
            "Missing Required": ", ".join(missing),
            "Positions": positions,
        })

        print(
            f"{'✅' if status == 'READY' else '⚠️'} "
            f"{path.name:<38} "
            f"{len(players):>5} players | "
            f"{len(df.columns):>3} cols | "
            f"{status}"
        )

    except Exception as e:

        audit.append({
            "Database": path.name,
            "Status": f"ERROR — {e}",
            "Sheet": "",
            "Players": 0,
            "Columns": 0,
            "Missing Required": "",
            "Positions": "",
        })

        print(f"❌ {path.name}: {e}")


audit_df = pd.DataFrame(audit)

players_df = pd.DataFrame(players_global)

if not players_df.empty:

    duplicate_players = (
        players_df
        .groupby("Player")
        .agg(
            Databases=("Database", "nunique"),
            Sources=("Database", lambda x: " | ".join(sorted(set(x))))
        )
        .reset_index()
    )

    duplicate_players = duplicate_players[
        duplicate_players["Databases"] > 1
    ].sort_values(
        ["Databases", "Player"],
        ascending=[False, True]
    )

else:

    duplicate_players = pd.DataFrame(
        columns=["Player", "Databases", "Sources"]
    )


# ============================================================
# SUMMARY
# ============================================================

ready = (audit_df["Status"] == "READY").sum()
warnings = (audit_df["Status"] == "WARNING").sum()
errors = audit_df["Status"].astype(str).str.startswith("ERROR").sum()

total_players = audit_df["Players"].sum()

print()
print("=" * 110)
print("SCOUTVISION — DATABASE AUDIT SUMMARY")
print("=" * 110)

print(f"Databases:          {len(files)}")
print(f"Ready:              {ready}")
print(f"Warnings:           {warnings}")
print(f"Errors:             {errors}")
print(f"Total player rows:  {total_players}")
print(f"Cross-db duplicates:{len(duplicate_players)}")

print()

if not duplicate_players.empty:
    print("TOP CROSS-DATABASE DUPLICATES")
    print("-" * 110)
    print(
        duplicate_players
        .head(30)
        .to_string(index=False)
    )

# ============================================================
# EXPORT
# ============================================================

output_file = OUTPUT_DIR / "scoutvision_database_audit.xlsx"

with pd.ExcelWriter(
    output_file,
    engine="openpyxl",
) as writer:

    audit_df.to_excel(
        writer,
        sheet_name="Database Audit",
        index=False,
    )

    duplicate_players.to_excel(
        writer,
        sheet_name="Cross DB Duplicates",
        index=False,
    )

    players_df.to_excel(
        writer,
        sheet_name="Player Registry",
        index=False,
    )

print()
print("=" * 110)
print("✅ DATABASE AUDIT GENERATED")
print("=" * 110)
print(f"Output: {output_file}")
