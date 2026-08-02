"""
01_prepare_scouting_database.py

Pregătește o bază de scouting pentru jucători de câmp:
- maximum 25 de ani;
- fără portari;
- standardizare pe familii de posturi;
- separare între Main Ranking, Emerging Watchlist și Insufficient Sample;
- salvare într-un fișier Excel pregătit pentru scoring.

Fișier de intrare:
    L3-France.xlsx

Fișier rezultat:
    France_L3_U25_prepared.xlsx
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "L3-France.xlsx"
OUTPUT_FILE = BASE_DIR / "France_L3_U25_prepared.xlsx"

MAX_AGE = 25
MIN_MATCHES_MAIN = 15
MIN_MATCHES_WATCHLIST = 8


POSITION_GROUP_ORDER = [
    "CB",
    "FB_WB",
    "DM",
    "CM",
    "AM",
    "Winger",
    "ST",
    "Other",
]


def normalize_position_text(position: object) -> set[str]:
    """Transformă textul poziției într-un set standardizat de coduri."""
    if pd.isna(position):
        return set()

    return {
        item.strip().upper()
        for item in str(position).split(",")
        if item.strip()
    }


def classify_position(position: object) -> str:
    """
    Atribuie o familie tactică principală.

    Ordinea este intenționată pentru jucătorii cu mai multe poziții:
    ST > Winger > AM > DM > CM > FB/WB > CB.
    """
    positions = normalize_position_text(position)

    if not positions:
        return "Other"

    # Portarii sunt identificați pentru a fi eliminați ulterior.
    if positions & {"GK"}:
        return "GK"

    # Atacanți centrali
    if positions & {
        "CF",
        "ST",
    }:
        return "ST"

    # Extreme și atacanți laterali
    if positions & {
        "LW",
        "RW",
        "LWF",
        "RWF",
        "LAMF",
        "RAMF",
    }:
        return "Winger"

    # Mijlocași ofensivi centrali
    if positions & {
        "AMF",
        "CAM",
    }:
        return "AM"

    # Mijlocași defensivi
    if positions & {
        "DMF",
        "LDMF",
        "RDMF",
        "CDM",
    }:
        return "DM"

    # Mijlocași centrali
    if positions & {
        "CMF",
        "LCMF",
        "RCMF",
        "CM",
    }:
        return "CM"

    # Fundași laterali și wing-back
    if positions & {
        "LB",
        "RB",
        "LWB",
        "RWB",
    }:
        return "FB_WB"

    # Fundași centrali
    if positions & {
        "CB",
        "LCB",
        "RCB",
    }:
        return "CB"

    return "Other"


def classify_age_profile(age: int) -> str:
    """Împarte jucătorii în două categorii de recrutare."""
    if age <= 21:
        return "Elite Prospect (≤21)"
    return "First-Team Ready (22–25)"


def classify_sample(matches_played: int) -> str:
    """Clasifică fiabilitatea eșantionului după numărul de meciuri."""
    if matches_played >= MIN_MATCHES_MAIN:
        return "Main Ranking"

    if matches_played >= MIN_MATCHES_WATCHLIST:
        return "Emerging Watchlist"

    return "Insufficient Sample"


def validate_columns(df: pd.DataFrame) -> None:
    required_columns = {
        "Player",
        "Team",
        "Position",
        "Age",
        "Matches played",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Lipsesc următoarele coloane obligatorii: "
            f"{sorted(missing)}"
        )


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    for column in ["Player", "Team", "Position"]:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
        )

    return cleaned


def sort_players(df: pd.DataFrame) -> pd.DataFrame:
    """Sortează logic jucătorii pentru verificare și raportare."""
    if df.empty:
        return df.copy()

    sorted_df = df.copy()

    sorted_df["Position Group"] = pd.Categorical(
        sorted_df["Position Group"],
        categories=POSITION_GROUP_ORDER,
        ordered=True,
    )

    sorted_df = sorted_df.sort_values(
        by=[
            "Position Group",
            "Age",
            "Matches played",
            "Player",
        ],
        ascending=[
            True,
            True,
            False,
            True,
        ],
    ).reset_index(drop=True)

    sorted_df["Position Group"] = (
        sorted_df["Position Group"]
        .astype("string")
    )

    return sorted_df


def create_summary(
    all_u25: pd.DataFrame,
    main_ranking: pd.DataFrame,
    watchlist: pd.DataFrame,
    insufficient: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for position_group in POSITION_GROUP_ORDER:
        all_count = int(
            (all_u25["Position Group"] == position_group).sum()
        )
        main_count = int(
            (main_ranking["Position Group"] == position_group).sum()
        )
        watch_count = int(
            (watchlist["Position Group"] == position_group).sum()
        )
        insufficient_count = int(
            (insufficient["Position Group"] == position_group).sum()
        )

        if all_count == 0:
            continue

        rows.append(
            {
                "Position Group": position_group,
                "All U25": all_count,
                "Main Ranking": main_count,
                "Emerging Watchlist": watch_count,
                "Insufficient Sample": insufficient_count,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Nu am găsit fișierul:\n{INPUT_FILE}\n\n"
            "Pune L3-France.xlsx în același folder cu scriptul."
        )

    df = pd.read_excel(INPUT_FILE)
    df.columns = df.columns.astype(str).str.strip()

    validate_columns(df)
    df = clean_text_columns(df)

    # Conversie sigură pentru coloanele-cheie.
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Matches played"] = pd.to_numeric(
        df["Matches played"],
        errors="coerce",
    )

    # Elimină rândurile fără vârstă sau număr de meciuri.
    df = df.dropna(
        subset=[
            "Player",
            "Age",
            "Matches played",
        ]
    ).copy()

    df["Age"] = df["Age"].astype(int)
    df["Matches played"] = df["Matches played"].astype(int)

    # Standardizarea posturilor.
    df.insert(
        3,
        "Position Group",
        df["Position"].apply(classify_position),
    )

    # Filtru de recrutare: maximum 25 de ani.
    u25 = df[df["Age"] <= MAX_AGE].copy()

    # Portarii sunt eliminați complet.
    u25 = u25[u25["Position Group"] != "GK"].copy()

    # Coloane contextuale pentru raport.
    u25.insert(
        5,
        "Age Profile",
        u25["Age"].apply(classify_age_profile),
    )

    u25.insert(
        7,
        "Sample Category",
        u25["Matches played"].apply(classify_sample),
    )

    # Separarea loturilor.
    main_ranking = u25[
        u25["Matches played"] >= MIN_MATCHES_MAIN
    ].copy()

    watchlist = u25[
        u25["Matches played"].between(
            MIN_MATCHES_WATCHLIST,
            MIN_MATCHES_MAIN - 1,
        )
    ].copy()

    insufficient = u25[
        u25["Matches played"] < MIN_MATCHES_WATCHLIST
    ].copy()

    # Sortare logică.
    u25 = sort_players(u25)
    main_ranking = sort_players(main_ranking)
    watchlist = sort_players(watchlist)
    insufficient = sort_players(insufficient)

    summary = create_summary(
        all_u25=u25,
        main_ranking=main_ranking,
        watchlist=watchlist,
        insufficient=insufficient,
    )

    # Salvarea rezultatului.
    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:
        main_ranking.to_excel(
            writer,
            sheet_name="Main Ranking Pool",
            index=False,
        )

        watchlist.to_excel(
            writer,
            sheet_name="Emerging Watchlist",
            index=False,
        )

        insufficient.to_excel(
            writer,
            sheet_name="Insufficient Sample",
            index=False,
        )

        u25.to_excel(
            writer,
            sheet_name="All U25",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

    print("=" * 68)
    print("FRANCE NATIONAL U25 SCOUTING DATABASE")
    print("=" * 68)

    print(f"Jucători inițiali:              {len(df)}")
    print(f"Jucători de câmp U25:           {len(u25)}")
    print(
        f"Main Ranking (≥{MIN_MATCHES_MAIN} meciuri): "
        f"{len(main_ranking)}"
    )
    print(
        f"Emerging Watchlist "
        f"({MIN_MATCHES_WATCHLIST}–{MIN_MATCHES_MAIN - 1} meciuri): "
        f"{len(watchlist)}"
    )
    print(
        f"Insufficient Sample "
        f"(<{MIN_MATCHES_WATCHLIST} meciuri): "
        f"{len(insufficient)}"
    )

    print("\nDistribuția pe posturi — Main Ranking:")
    if main_ranking.empty:
        print("Nu există jucători eligibili.")
    else:
        print(
            main_ranking["Position Group"]
            .value_counts()
            .reindex(POSITION_GROUP_ORDER)
            .dropna()
            .astype(int)
        )

    print(f"\nFișier creat:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nEROARE:\n{exc}")
        sys.exit(1)
