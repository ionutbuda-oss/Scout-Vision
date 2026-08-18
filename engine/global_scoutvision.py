from pathlib import Path
import pandas as pd

INPUT_FILE = Path(
    "outputs/global_database/scoutvision_global_unique.xlsx"
)

OUTPUT_DIR = Path(
    "outputs/global_scoutvision"
)

OUTPUT_FILE = OUTPUT_DIR / "global_player_pool.xlsx"

REQUIRED_COLUMNS = [
    "Player",
    "Team",
    "Age",
    "Position",
    "Matches played",
    "Minutes played",
]


def main():

    print("=" * 110)
    print("SCOUTVISION — GLOBAL POOL V1")
    print("=" * 110)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="Global Unique",
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    print(f"Input players: {len(df)}")
    print(f"Input columns: {len(df.columns)}")

    # ---------------------------------------------------------
    # STRUCTURE VALIDATION
    # ---------------------------------------------------------

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print("Required columns: OK")

    # ---------------------------------------------------------
    # BASIC CLEANING
    # ---------------------------------------------------------

    df["Player"] = (
        df["Player"]
        .astype(str)
        .str.strip()
    )

    df["Team"] = (
        df["Team"]
        .astype(str)
        .str.strip()
    )

    df["Position"] = (
        df["Position"]
        .astype(str)
        .str.strip()
    )

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
    )

    # ---------------------------------------------------------
    # POSITION GROUP
    # ---------------------------------------------------------

    if "Position Group" not in df.columns:

        from engine.prepare_database import classify_position

        df["Position Group"] = (
            df["Position"]
            .apply(classify_position)
        )

    # ---------------------------------------------------------
    # SCOUTVISION PRE-SCORING FIELDS
    # ---------------------------------------------------------

    from engine.config import Settings
    from engine.prepare_database import (
        classify_age_profile,
        classify_sample,
    )

    settings = Settings()

    df["Age Profile"] = (
        df["Age"]
        .apply(classify_age_profile)
    )

    df["Sample Category"] = (
        df["Matches played"]
        .apply(
            lambda matches: classify_sample(
                matches,
                settings,
            )
        )
    )

    # ---------------------------------------------------------
    # BASIC ELIGIBILITY
    # ---------------------------------------------------------

    df["Global Eligible"] = (
        df["Player"].ne("")
        & df["Age"].notna()
        & df["Position"].ne("")
    )

    # ---------------------------------------------------------
    # GLOBAL PLAYER ID
    # ---------------------------------------------------------

    df.insert(
        0,
        "Global Player ID",
        [
            f"P{i:06d}"
            for i in range(1, len(df) + 1)
        ],
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    position_counts = (
        df["Position Group"]
        .value_counts()
        .sort_index()
    )

    print()
    print("POSITION GROUPS")
    print("-" * 110)

    for position, count in position_counts.items():
        print(
            f"{str(position):<15} {count:>6}"
        )

    print()
    print(
        f"Eligible players: "
        f"{int(df['Global Eligible'].sum())}"
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

        df.to_excel(
            writer,
            sheet_name="Global Pool",
            index=False,
        )

        position_summary = position_counts.rename("Players").reset_index()
        position_summary.columns = ["Position Group", "Players"]

        position_summary.to_excel(
            writer,
            sheet_name="Position Summary",
            index=False,
        )

    print()
    print("=" * 110)
    print("✅ GLOBAL POOL V1 GENERATED")
    print("=" * 110)
    print(f"Players: {len(df)}")
    print(f"Output:  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
