from pathlib import Path

import pandas as pd

from engine.config import Settings
from engine.prepare_database import (
    validate_columns,
    clean_text_columns,
    classify_position,
)
from engine.score_players import (
    ROLE_MODELS,
    score_position_group,
)


DATABASES = {
    "SPAIN 2": "L2_Spain.xlsx",
    "CZECHIA 1": "Liga 1-Cehia.xlsx",
    "SERBIA 1": "Liga 1-Serbia.xlsx",
    "PORTUGAL 2": "Liga 2-Portugal.xlsx",
}

TODAY = pd.Timestamp("2026-08-17")

MIN_MINUTES = 900
MIN_MATCHES = 10


def prepare_all_players(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

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

    df["Minutes played"] = pd.to_numeric(
        df["Minutes played"],
        errors="coerce",
    ).fillna(0)

    df = df.dropna(
        subset=[
            "Player",
            "Age",
            "Matches played",
        ]
    ).copy()

    df["Age"] = df["Age"].astype(int)
    df["Matches played"] = df["Matches played"].astype(int)

    df.insert(
        3,
        "Position Group",
        df["Position"].apply(classify_position),
    )

    # ScoutVision recruitment model excludes goalkeepers.
    df = df[
        df["Position Group"] != "GK"
    ].copy()

    # Required by the existing ScoutVision scoring engine.
    def age_profile(age):
        if age <= 21:
            return "U21"
        if age <= 23:
            return "U23"
        if age <= 25:
            return "U25"
        if age <= 28:
            return "Prime"
        if age <= 31:
            return "Experienced"
        return "Veteran"

    df["Age Profile"] = df["Age"].apply(age_profile)

    # Required by the existing scoring/report pipeline.
    df["Sample Category"] = df["Matches played"].apply(
        lambda matches:
            "Strong Sample" if matches >= 15
            else "Adequate Sample" if matches >= 10
            else "Limited Sample"
    )

    return df


def identify_free_agent_candidates(
    df: pd.DataFrame,
    league: str,
) -> pd.DataFrame:

    df = df.copy()

    df["Contract Status"] = "UNKNOWN — VERIFY"

    if "Contract expires" in df.columns:

        df["Contract expires"] = pd.to_datetime(
            df["Contract expires"],
            errors="coerce",
        )

        explicit_expired = (
            df["Contract expires"].notna()
            & (df["Contract expires"] <= TODAY)
        )

        active_contract = (
            df["Contract expires"].notna()
            & (df["Contract expires"] > TODAY)
        )

        unknown_contract = (
            df["Contract expires"].isna()
        )

        df.loc[
            explicit_expired,
            "Contract Status"
        ] = "EXPIRED — VERIFY"

        df.loc[
            active_contract,
            "Contract Status"
        ] = "ACTIVE CONTRACT"

        df.loc[
            unknown_contract,
            "Contract Status"
        ] = "UNKNOWN — VERIFY"

    df["League"] = league

    adequate_sample = (
        (df["Minutes played"] >= MIN_MINUTES)
        & (df["Matches played"] >= MIN_MATCHES)
    )

    candidates = df[
        adequate_sample
        & df["Contract Status"].isin(
            [
                "EXPIRED — VERIFY",
                "UNKNOWN — VERIFY",
            ]
        )
    ].copy()

    return candidates


def main():

    print("=" * 90)
    print("SCOUTVISION — FREE AGENT SCOUTING ENGINE")
    print("=" * 90)

    all_results = []

    for league, filename in DATABASES.items():

        print()
        print("-" * 90)
        print(league)

        input_file = (
            Path("databases")
            / filename
        )

        df = pd.read_excel(
            input_file
        )

        print(
            "Players loaded:",
            len(df)
        )

        prepared = prepare_all_players(
            df
        )

        print(
            "Outfield players:",
            len(prepared)
        )

        candidates = identify_free_agent_candidates(
            prepared,
            league,
        )

        print(
            "Candidate pool:",
            len(candidates)
        )

        if candidates.empty:
            continue

        scored_groups = []

        for position_group in ROLE_MODELS:

            group = prepared[
                prepared["Position Group"]
                == position_group
            ].copy()

            if group.empty:
                continue

            # IMPORTANT:
            # Score the complete league position pool.
            # This preserves correct within-position percentiles.
            scored = score_position_group(
                group_df=group,
                position_group=position_group,
            )

            candidate_names = set(
                candidates["Player"]
                .astype(str)
                .str.strip()
                .str.casefold()
            )

            scored = scored[
                scored["Player"]
                .astype(str)
                .str.strip()
                .str.casefold()
                .isin(candidate_names)
            ].copy()

            if scored.empty:
                continue

            scored_groups.append(
                scored
            )

        if not scored_groups:
            continue

        league_results = pd.concat(
            scored_groups,
            ignore_index=True,
            sort=False,
        )

        status_lookup = candidates.set_index(
            candidates["Player"]
            .astype(str)
            .str.strip()
            .str.casefold()
        )["Contract Status"].to_dict()

        league_results["League"] = league

        league_results["Contract Status"] = (
            league_results["Player"]
            .astype(str)
            .str.strip()
            .str.casefold()
            .map(status_lookup)
        )

        all_results.append(
            league_results
        )

        print(
            "Scored candidates:",
            len(league_results)
        )

    if not all_results:

        print()
        print("No candidates found.")
        return

    result = pd.concat(
        all_results,
        ignore_index=True,
        sort=False,
    )

    result = result.sort_values(
        [
            "Scout Score",
            "Performance Score",
            "Minutes played",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).reset_index(drop=True)

    result.insert(
        0,
        "Free Agent Rank",
        range(1, len(result) + 1),
    )

    output_dir = Path(
        "outputs/free_agents"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / "free_agents_scoutvision_rankings.xlsx"
    )

    front_columns = [
        "Free Agent Rank",
        "League",
        "Player",
        "Team",
        "Position",
        "Position Group",
        "Age",
        "Contract Status",
        "Contract expires",
        "Matches played",
        "Minutes played",
        "Scout Score",
        "Performance Score",
        "Recommendation",
        "Age Potential Score",
        "Sample Confidence",
    ]

    front_columns = [
        c
        for c in front_columns
        if c in result.columns
    ]

    remaining = [
        c
        for c in result.columns
        if c not in front_columns
    ]

    result = result[
        front_columns + remaining
    ]

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl",
    ) as writer:

        result.to_excel(
            writer,
            sheet_name="All Free Agent Candidates",
            index=False,
        )

        for position_group in ROLE_MODELS:

            group = result[
                result["Position Group"]
                == position_group
            ].copy()

            if group.empty:
                continue

            group.to_excel(
                writer,
                sheet_name=position_group[:31],
                index=False,
            )

    print()
    print("=" * 90)
    print("FREE AGENT SCOUTVISION RANKING COMPLETE")
    print("=" * 90)
    print(
        "Total candidates:",
        len(result)
    )

    print()

    for position_group in ROLE_MODELS:

        group = result[
            result["Position Group"]
            == position_group
        ]

        if group.empty:
            continue

        top = group.iloc[0]

        print(
            f"{position_group:8} | "
            f"{top['Player']} | "
            f"{top['Scout Score']:.1f} | "
            f"{top['Recommendation']}"
        )

    print()
    print("Output:")
    print(output_file)


if __name__ == "__main__":
    main()
