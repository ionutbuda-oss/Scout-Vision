from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "outputs/free_agents/free_agents_scoutvision_rankings.xlsx"
)

OUTPUT_FILE = Path(
    "outputs/free_agents/free_agent_verification_priority.xlsx"
)

TOP_N = 30


def normalize(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(100.0, index=series.index)

    return ((series - minimum) / (maximum - minimum) * 100).round(1)


def main():

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="All Free Agent Candidates",
    )

    print("=" * 90)
    print("SCOUTVISION — FREE AGENT VERIFICATION PRIORITY")
    print("=" * 90)

    # ---------------------------------------------------------
    # Remove players already known to be unavailable
    # ---------------------------------------------------------

    excluded = {
        "R. Macek",
    }

    df = df[
        ~df["Player"].astype(str).isin(excluded)
    ].copy()

    # ---------------------------------------------------------
    # Scout Score component
    # ---------------------------------------------------------

    df["Scout Component"] = normalize(
        df["Scout Score"]
    )

    # ---------------------------------------------------------
    # Performance component
    # ---------------------------------------------------------

    df["Performance Component"] = normalize(
        df["Performance Score"]
    )

    # ---------------------------------------------------------
    # Sample reliability
    # ---------------------------------------------------------

    minutes = pd.to_numeric(
        df.get("Minutes played", 0),
        errors="coerce",
    ).fillna(0)

    matches = pd.to_numeric(
        df.get("Matches played", 0),
        errors="coerce",
    ).fillna(0)

    minute_score = (
        minutes.clip(upper=3000) / 3000 * 100
    )

    match_score = (
        matches.clip(upper=35) / 35 * 100
    )

    df["Sample Component"] = (
        minute_score * 0.65
        + match_score * 0.35
    ).round(1)

    # ---------------------------------------------------------
    # Age suitability
    #
    # Prime recruitment window receives the strongest score.
    # Older players are still eligible — they are simply
    # treated as different recruitment profiles.
    # ---------------------------------------------------------

    def age_score(age):

        try:
            age = float(age)
        except Exception:
            return 50.0

        if age <= 23:
            return 100.0
        if age <= 26:
            return 95.0
        if age <= 29:
            return 90.0
        if age <= 32:
            return 80.0
        if age <= 35:
            return 65.0

        return 45.0

    df["Age Component"] = (
        df["Age"].apply(age_score)
    )

    # ---------------------------------------------------------
    # Final Verification Priority Score
    #
    # 40% Scout
    # 30% Performance
    # 15% Sample
    # 15% Age
    # ---------------------------------------------------------

    df["Verification Priority Score"] = (
        df["Scout Component"] * 0.40
        + df["Performance Component"] * 0.30
        + df["Sample Component"] * 0.15
        + df["Age Component"] * 0.15
    ).round(1)

    # ---------------------------------------------------------
    # Priority label
    # ---------------------------------------------------------

    def priority_label(score):

        if score >= 85:
            return "VERY HIGH"

        if score >= 75:
            return "HIGH"

        if score >= 65:
            return "MEDIUM"

        return "LOW"

    df["Verification Priority"] = (
        df["Verification Priority Score"]
        .apply(priority_label)
    )

    # ---------------------------------------------------------
    # Sort
    # ---------------------------------------------------------

    df = df.sort_values(
        [
            "Verification Priority Score",
            "Scout Score",
            "Performance Score",
        ],
        ascending=False,
    ).reset_index(drop=True)

    df.insert(
        0,
        "Verification Rank",
        range(1, len(df) + 1),
    )

    # ---------------------------------------------------------
    # Output columns
    # ---------------------------------------------------------

    columns = [
        "Verification Rank",
        "League",
        "Player",
        "Team",
        "Age",
        "Position Group",
        "Matches played",
        "Minutes played",
        "Scout Score",
        "Performance Score",
        "Contract Status",
        "Verification Priority Score",
        "Verification Priority",
        "Recommendation",
    ]

    columns = [
        c for c in columns
        if c in df.columns
    ]

    top = df.head(TOP_N)[columns]

    # ---------------------------------------------------------
    # Excel
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        top.to_excel(
            writer,
            sheet_name="Top 30 Verify",
            index=False,
        )

        df[columns].to_excel(
            writer,
            sheet_name="All Candidates",
            index=False,
        )

    # ---------------------------------------------------------
    # Console
    # ---------------------------------------------------------

    print()
    print("Candidates analysed:", len(df))
    print("Top verification candidates:", len(top))
    print()
    print(top.to_string(index=False))
    print()
    print("=" * 90)
    print("✅ VERIFICATION PRIORITY BOARD GENERATED")
    print("=" * 90)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
