from pathlib import Path
import pandas as pd

from engine.score_players import score_position_group

INPUT_FILE = Path(
    "outputs/global_scoutvision/global_player_pool.xlsx"
)

OUTPUT_DIR = Path(
    "outputs/global_scoutvision"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "global_cross_league_scoring.xlsx"
)

POSITION_GROUPS = [
    "CB",
    "FB_WB",
    "DM",
    "CM",
    "AM",
    "Winger",
    "ST",
]


def main():

    print("=" * 110)
    print("SCOUTVISION — CROSS-LEAGUE SCORING V1")
    print("=" * 110)

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Global Pool",
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    print(f"Input players: {len(df)}")
    print(f"Input columns: {len(df.columns)}")

    scored_groups = []

    print()
    print("GLOBAL POSITION SCORING")
    print("-" * 110)

    for position_group in POSITION_GROUPS:

        group = df[
            df["Position Group"]
            .astype(str)
            .str.strip()
            == position_group
        ].copy()

        if group.empty:
            continue

        print(
            f"{position_group:<12}"
            f"{len(group):>6} players"
        )

        scored = score_position_group(
            group_df=group,
            position_group=position_group,
        )

        scored_groups.append(scored)

    if not scored_groups:
        raise ValueError(
            "No position groups could be scored."
        )

    scored_all = pd.concat(
        scored_groups,
        ignore_index=True,
        sort=False,
    )

    # ---------------------------------------------------------
    # COMPETENCY SCORE COLUMNS
    # ---------------------------------------------------------

    score_columns = [
        c for c in scored_all.columns
        if c.endswith(" Score")
        and c not in {
            "Scout Score",
            "Performance Score",
            "Age Potential Score",
            "Recruitment Score",
        }
    ]

    print()
    print(
        f"Competency score columns: "
        f"{len(score_columns)}"
    )

    # ---------------------------------------------------------
    # CROSS-LEAGUE PERCENTILES
    # ---------------------------------------------------------

    for position_group in POSITION_GROUPS:

        mask = (
            scored_all["Position Group"]
            .astype(str)
            .str.strip()
            == position_group
        )

        if not mask.any():
            continue

        for column in score_columns:

            output_column = (
                "Global PCTL | "
                + column.replace(" Score", "")
            )

            values = pd.to_numeric(
                scored_all.loc[mask, column],
                errors="coerce",
            )

            scored_all.loc[
                mask,
                output_column
            ] = values.rank(
                pct=True,
                method="average",
            ) * 100

    # ---------------------------------------------------------
    # CROSS-LEAGUE SCORE
    # ---------------------------------------------------------

    global_percentile_columns = [
        c for c in scored_all.columns
        if c.startswith("Global PCTL | ")
    ]

    if not global_percentile_columns:
        raise ValueError(
            "No global percentile columns were generated."
        )

    scored_all["Cross-League Score"] = (
        scored_all[
            global_percentile_columns
        ]
        .mean(
            axis=1,
            skipna=True,
        )
    )

    # ---------------------------------------------------------
    # POSITION RANK
    # ---------------------------------------------------------

    scored_all[
        "Cross-League Position Rank"
    ] = pd.NA

    for position_group in POSITION_GROUPS:

        mask = (
            scored_all["Position Group"]
            .astype(str)
            .str.strip()
            == position_group
        )

        if not mask.any():
            continue

        scored_all.loc[
            mask,
            "Cross-League Position Rank"
        ] = (
            scored_all.loc[
                mask,
                "Cross-League Score"
            ]
            .rank(
                ascending=False,
                method="min",
            )
        )

    # ---------------------------------------------------------
    # EXPORT
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        scored_all.to_excel(
            writer,
            sheet_name="Global Ranked",
            index=False,
        )

        summary = (
            scored_all
            .groupby("Position Group")
            .agg(
                Players=("Player", "count"),
                Mean_Score=(
                    "Cross-League Score",
                    "mean",
                ),
                Max_Score=(
                    "Cross-League Score",
                    "max",
                ),
            )
            .reset_index()
        )

        summary.to_excel(
            writer,
            sheet_name="Position Summary",
            index=False,
        )

    # ---------------------------------------------------------
    # TOP 20 FB_WB
    # ---------------------------------------------------------

    print()
    print("=" * 110)
    print("TOP 20 GLOBAL FB_WB")
    print("=" * 110)

    fb = scored_all[
        scored_all["Position Group"]
        .astype(str)
        .str.strip()
        == "FB_WB"
    ].copy()

    fb = fb.sort_values(
        "Cross-League Score",
        ascending=False,
    )

    columns = [
        "Player",
        "Team",
        "Age",
        "Position",
        "Scout Score",
        "Cross-League Score",
        "Cross-League Position Rank",
    ]

    print(
        fb[columns]
        .head(20)
        .to_string(index=False)
    )

    print()
    print("=" * 110)
    print("✅ CROSS-LEAGUE SCORING V1 GENERATED")
    print("=" * 110)
    print(f"Players: {len(scored_all)}")
    print(f"Competencies: {len(score_columns)}")
    print(f"Global PCTL columns: {len(global_percentile_columns)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
