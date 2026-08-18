from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine.config import Settings


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


def primary_position_token(position: object) -> str:
    """Return the first Wyscout position token as the primary position.

    Wyscout lists positions in priority order. ScoutVision therefore maps a
    player from the first non-empty token instead of searching all secondary
    positions using a fixed priority hierarchy.
    """

    if pd.isna(position):
        return ""

    for item in str(position).split(","):
        token = item.strip().upper()
        if token:
            return token

    return ""


def classify_position(position: object) -> str:
    primary = primary_position_token(position)

    if not primary:
        return "Other"

    if primary == "GK":
        return "GK"

    if primary in {"CF", "ST"}:
        return "ST"

    if primary in {
        "LW", "RW", "LWF", "RWF",
        "LAMF", "RAMF",
    }:
        return "Winger"

    if primary in {"AMF", "CAM"}:
        return "AM"

    if primary in {
        "DMF", "LDMF", "RDMF", "CDM",
    }:
        return "DM"

    if primary in {
        "CMF", "LCMF", "RCMF", "CM",
    }:
        return "CM"

    if primary in {
        "LB", "RB", "LWB", "RWB",
    }:
        return "FB_WB"

    if primary in {
        "CB", "LCB", "RCB",
    }:
        return "CB"

    return "Other"


def classify_age_profile(age: int) -> str:
    if age <= 21:
        return "Elite Prospect (≤21)"

    return "First-Team Ready (22–25)"


def classify_sample(matches_played: int, settings: Settings) -> str:
    if matches_played >= settings.minimum_matches:
        return "Main Ranking"

    if matches_played >= 8:
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
            "Lipsesc coloanele obligatorii: "
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

        if all_count == 0:
            continue

        rows.append(
            {
                "Position Group": position_group,
                "All U25": all_count,
                "Main Ranking": int(
                    (
                        main_ranking["Position Group"]
                        == position_group
                    ).sum()
                ),
                "Emerging Watchlist": int(
                    (
                        watchlist["Position Group"]
                        == position_group
                    ).sum()
                ),
                "Insufficient Sample": int(
                    (
                        insufficient["Position Group"]
                        == position_group
                    ).sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def prepare_database(settings: Settings) -> dict[str, int]:
    df = pd.read_excel(settings.database_file)
    df.columns = df.columns.astype(str).str.strip()

    validate_columns(df)
    df = clean_text_columns(df)

    df["Age"] = pd.to_numeric(
        df["Age"],
        errors="coerce",
    )
    df["Matches played"] = pd.to_numeric(
        df["Matches played"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "Player",
            "Age",
            "Matches played",
        ]
    ).copy()

    df["Age"] = df["Age"].astype(int)
    df["Matches played"] = (
        df["Matches played"].astype(int)
    )

    df.insert(
        3,
        "Position Group",
        df["Position"].apply(classify_position),
    )

    u25 = df[
        df["Age"] <= settings.max_age
    ].copy()

    u25 = u25[
        u25["Position Group"] != "GK"
    ].copy()

    u25.insert(
        5,
        "Age Profile",
        u25["Age"].apply(classify_age_profile),
    )

    u25.insert(
        7,
        "Sample Category",
        u25["Matches played"].apply(
            lambda matches: classify_sample(
                matches,
                settings,
            )
        ),
    )

    main_ranking = u25[
        u25["Matches played"]
        >= settings.minimum_matches
    ].copy()

    watchlist = u25[
        u25["Matches played"].between(
            8,
            settings.minimum_matches - 1,
        )
    ].copy()

    insufficient = u25[
        u25["Matches played"] < 8
    ].copy()

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

    settings.prepared_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        settings.prepared_file,
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

    return {
        "original_players": len(df),
        "u25_outfield_players": len(u25),
        "main_ranking_players": len(main_ranking),
        "watchlist_players": len(watchlist),
        "insufficient_players": len(insufficient),
    }


if __name__ == "__main__":
    settings = Settings()

    result = prepare_database(settings)

    print("✅ Database prepared")
    print(settings.prepared_file)

    for key, value in result.items():
        print(f"{key}: {value}")
