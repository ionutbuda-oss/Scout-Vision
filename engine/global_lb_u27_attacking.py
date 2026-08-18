from pathlib import Path
import pandas as pd

INPUT_FILE = Path(
    "outputs/global_scoutvision/global_cross_league_scoring.xlsx"
)

OUTPUT_DIR = Path(
    "outputs/global_scoutvision"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "global_lb_u27_attacking.xlsx"
)


def main():

    print("=" * 110)
    print("SCOUTVISION — GLOBAL U27 ATTACKING LEFT-BACK BOARD")
    print("=" * 110)

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Global Ranked",
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------------
    # FILTER LB / LWB U27
    # ---------------------------------------------------------

    position_text = (
        df["Position"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    mask = (
        df["Age"].between(16, 26, inclusive="both")
        &
        position_text.str.contains(
            r"\bLB\b|\bLWB\b",
            regex=True,
            na=False,
        )
    )

    lb = df.loc[mask].copy()

    print(f"Global players: {len(df)}")
    print(f"U27 LB/LWB candidates: {len(lb)}")

    # ---------------------------------------------------------
    # ATTACKING COMPONENTS
    # ---------------------------------------------------------

    def get_column(name):
        candidates = [
            f"{name} Score",
            f"Global PCTL | {name}",
        ]

        for column in candidates:
            if column in lb.columns:
                return column

        return None

    progression = get_column("Progression")
    chance_creation = get_column("Chance Creation")
    ball_carrying = get_column("Ball Carrying")

    if not progression:
        raise ValueError(
            "Progression score missing."
        )

    if not chance_creation:
        raise ValueError(
            "Chance Creation score missing."
        )

    if not ball_carrying:
        raise ValueError(
            "Ball Carrying score missing."
        )

    # ---------------------------------------------------------
    # ATTACKING LB INDEX
    # ---------------------------------------------------------

    lb["Attacking LB Index"] = (
        lb[progression] * 0.40
        + lb[chance_creation] * 0.30
        + lb[ball_carrying] * 0.30
    )

    # ---------------------------------------------------------
    # ARCHETYPE SCORE
    # ---------------------------------------------------------

    archetype_columns = [
        column
        for column in lb.columns
        if column.startswith("Global PCTL | ")
        and any(
            key in column
            for key in [
                "Progression",
                "Chance Creation",
                "Ball Carrying",
            ]
        )
    ]

    # ---------------------------------------------------------
    # RANK
    # ---------------------------------------------------------

    lb = lb.sort_values(
        [
            "Attacking LB Index",
            "Cross-League Score",
        ],
        ascending=False,
    ).reset_index(drop=True)

    lb.insert(
        0,
        "Attacking LB Rank",
        range(1, len(lb) + 1),
    )

    # ---------------------------------------------------------
    # OUTPUT COLUMNS
    # ---------------------------------------------------------

    preferred = [
        "Attacking LB Rank",
        "Player",
        "Team",
        "Source Database",
        "Age",
        "Position",
        "Position Group",
        "Matches played",
        "Minutes played",
        "Scout Score",
        "Cross-League Score",
        "Cross-League Position Rank",
        progression,
        chance_creation,
        ball_carrying,
        "Attacking LB Index",
        "Recommendation",
    ]

    columns = [
        column
        for column in preferred
        if column in lb.columns
    ]

    result = lb[columns].copy()

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

        result.to_excel(
            writer,
            sheet_name="Global LB U27",
            index=False,
        )

    # ---------------------------------------------------------
    # PRINT TOP 30
    # ---------------------------------------------------------

    print()
    print("=" * 110)
    print("TOP 30 GLOBAL U27 ATTACKING LB")
    print("=" * 110)

    print(
        result.head(30).to_string(
            index=False
        )
    )

    print()
    print("=" * 110)
    print("✅ GLOBAL LB U27 ATTACKING BOARD GENERATED")
    print("=" * 110)

    print(
        f"Candidates analysed: {len(result)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
