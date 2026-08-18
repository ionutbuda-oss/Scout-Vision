from pathlib import Path
import pandas as pd
import math

BASE = Path(".")
SHORTLIST = BASE / "outputs/global_scoutvision/scoutvision_romania_shortlist_21_master.xlsx"
DATABASES = BASE / "databases"

TOLERANCE = 1e-9


def norm_name(x):
    return str(x).strip().casefold()


def numeric(x):
    if pd.isna(x):
        return None
    try:
        return float(x)
    except Exception:
        return None


def equal_values(a, b):
    if pd.isna(a) and pd.isna(b):
        return True

    if pd.isna(a) or pd.isna(b):
        return False

    na = numeric(a)
    nb = numeric(b)

    if na is not None and nb is not None:
        return math.isclose(
            na,
            nb,
            rel_tol=1e-9,
            abs_tol=TOLERANCE,
        )

    return str(a).strip() == str(b).strip()


shortlist = pd.read_excel(
    SHORTLIST,
    sheet_name="All Ranked",
)

total_players = len(shortlist)
players_found = 0
players_checked = 0
players_with_mismatch = 0

total_fields_checked = 0
total_mismatches = 0

mismatches = []

print("=" * 110)
print("SCOUTVISION — ROMANIA DATA INTEGRITY V1")
print("=" * 110)
print(f"SHORTLIST PLAYERS: {total_players}")
print()

for _, target in shortlist.iterrows():

    player = str(target["Player"]).strip()
    team = str(target["Team"]).strip()
    source_name = str(target["Source Database"]).strip()

    source_path = DATABASES / source_name

    print(f"CHECKING: {player} | {team} | {source_name}")

    if not source_path.exists():
        print("  ERROR: source missing")
        continue

    source = None
    source_sheet = None

    try:
        xls = pd.ExcelFile(source_path)

        for sheet in xls.sheet_names:
            raw = pd.read_excel(
                source_path,
                sheet_name=sheet,
            )

            if "Player" not in raw.columns:
                continue

            matches = raw[
                raw["Player"].map(norm_name)
                == norm_name(player)
            ]

            # Prefer team match when available.
            if len(matches) > 1 and "Team" in raw.columns:
                team_matches = matches[
                    matches["Team"].map(norm_name)
                    == norm_name(team)
                ]

                if not team_matches.empty:
                    matches = team_matches

            if not matches.empty:
                source = matches.iloc[0]
                source_sheet = sheet
                players_found += 1
                break

        if source is None:
            print("  ERROR: player not found")
            continue

        players_checked += 1

        shared_columns = [
            col
            for col in shortlist.columns
            if col in source.index
        ]

        player_mismatches = []

        for col in shared_columns:

            # Ignore identifiers already used to locate the row.
            if col in {
                "Player",
                "Team",
                "Source Database",
            }:
                continue

            a = target[col]
            b = source[col]

            total_fields_checked += 1

            if not equal_values(a, b):
                total_mismatches += 1

                player_mismatches.append(
                    (col, a, b)
                )

                mismatches.append({
                    "Player": player,
                    "Team": team,
                    "Source Database": source_name,
                    "Source Sheet": source_sheet,
                    "Field": col,
                    "Shortlist Value": a,
                    "Source Value": b,
                })

        if player_mismatches:
            players_with_mismatch += 1

            print(
                f"  MISMATCHES: {len(player_mismatches)}"
            )

            for col, a, b in player_mismatches[:10]:
                print(
                    f"    {col}: "
                    f"SHORTLIST={a!r} | "
                    f"SOURCE={b!r}"
                )

            if len(player_mismatches) > 10:
                print(
                    f"    ... +{len(player_mismatches)-10} more"
                )

        else:
            print(
                f"  PASS | shared fields checked: "
                f"{len(shared_columns)-3}"
            )

    except Exception as exc:
        print(f"  ERROR: {exc}")

    print()

print("=" * 110)
print("DATA INTEGRITY RESULT")
print("=" * 110)
print(f"PLAYERS IN SHORTLIST       : {total_players}")
print(f"PLAYERS FOUND IN SOURCE    : {players_found}")
print(f"PLAYERS CHECKED            : {players_checked}")
print(f"PLAYERS WITH MISMATCHES    : {players_with_mismatch}")
print(f"FIELDS COMPARED            : {total_fields_checked}")
print(f"TOTAL MISMATCHES           : {total_mismatches}")
print()

if mismatches:
    audit_path = (
        BASE
        / "outputs/global_scoutvision/"
        / "scoutvision_romania_data_integrity_v1.xlsx"
    )

    audit_df = pd.DataFrame(mismatches)

    audit_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit_df.to_excel(
        audit_path,
        index=False,
    )

    print(f"AUDIT FILE: {audit_path}")
else:
    print("RESULT: ALL SHARED SOURCE VALUES MATCH")

print("=" * 110)
