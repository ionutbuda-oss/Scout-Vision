from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "outputs/free_agents/free_agents_scoutvision_rankings.xlsx"
)

OUTPUT_FILE = Path(
    "outputs/free_agents/free_agent_verification_priority_v2.xlsx"
)

TOP_N = 30


def normalize(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(100.0, index=series.index)

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    ).round(1)


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


def priority_label(score):
    if score >= 85:
        return "VERY HIGH"
    if score >= 75:
        return "HIGH"
    if score >= 65:
        return "MEDIUM"
    return "LOW"


def main():

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="All Free Agent Candidates",
    )

    print("=" * 90)
    print("SCOUTVISION — FREE AGENT VERIFICATION PRIORITY V2")
    print("=" * 90)

    # Known unavailable player identified during manual verification.
    excluded = {
        "R. Macek",
    }

    df = df[
        ~df["Player"].astype(str).isin(excluded)
    ].copy()

    # ---------------------------------------------------------
    # 1. FOOTBALL VALUE
    # ---------------------------------------------------------

    df["Scout Component"] = normalize(
        df["Scout Score"]
    )

    df["Performance Component"] = normalize(
        df["Performance Score"]
    )

    # ---------------------------------------------------------
    # 2. SAMPLE RELIABILITY
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
        minutes.clip(upper=3000)
        / 3000
        * 100
    )

    match_score = (
        matches.clip(upper=35)
        / 35
        * 100
    )

    df["Sample Component"] = (
        minute_score * 0.65
        + match_score * 0.35
    ).round(1)

    # ---------------------------------------------------------
    # 3. AGE SUITABILITY
    # ---------------------------------------------------------

    df["Age Component"] = (
        df["Age"]
        .apply(age_score)
        .round(1)
    )

    # ---------------------------------------------------------
    # 4. FINAL V2 SCORE
    #
    # Football value is now dominant:
    #
    # Scout Score       50%
    # Performance       20%
    # Sample             15%
    # Age                15%
    # ---------------------------------------------------------

    df["Verification Priority Score"] = (
        df["Scout Component"] * 0.50
        + df["Performance Component"] * 0.20
        + df["Sample Component"] * 0.15
        + df["Age Component"] * 0.15
    ).round(1)

    df["Verification Priority"] = (
        df["Verification Priority Score"]
        .apply(priority_label)
    )

    # ---------------------------------------------------------
    # 5. RANK
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
    # 6. OUTPUT
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
            sheet_name="Top 30 Verify V2",
            index=False,
        )

        df[columns].to_excel(
            writer,
            sheet_name="All Candidates V2",
            index=False,
        )

    # ---------------------------------------------------------
    # 7. CONSOLE
    # ---------------------------------------------------------

    print()
    print("Candidates analysed:", len(df))
    print("Top verification candidates:", len(top))
    print()

    print(
        top.to_string(index=False)
    )

    print()
    print("=" * 90)
    print("✅ VERIFICATION PRIORITY V2 GENERATED")
    print("=" * 90)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
