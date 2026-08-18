"""
Test Archetype Ranking Engine - ST profiles
"""

import pandas as pd

from engine.reports.archetype_ranking import (
    calculate_archetype_score,
)


FILE = "outputs/rankings/France_Ligue_3_U25_rankings.xlsx"


def main():

    df = pd.read_excel(
        FILE,
        sheet_name="All Ranked"
    )

    print("Players loaded:", len(df))

    # ST only
    st = df[
        df["Position Group"].astype(str).str.strip() == "ST"
    ].copy()

    print("ST players:", len(st))


    results = []

    for _, row in st.iterrows():

        metrics = {}

        # Competency scores from ranking file
        for col in [
            "Box Threat Score",
            "Offensive Duels Score",
            "Finishing Score",
            "Goal Threat Score",
        ]:

            if col in row.index and pd.notna(row[col]):
                name = col.replace(" Score", "")
                metrics[name] = float(row[col])


        score = calculate_archetype_score(
            metrics,
            "BOX STRIKER"
        )

        results.append(
            {
                "Player": row["Player"],
                "Team": row.get("Team", ""),
                "Score": score,
            }
        )


    result_df = pd.DataFrame(results)

    result_df = result_df.sort_values(
        "Score",
        ascending=False
    )

    print("\nTOP BOX STRIKERS")
    print(
        result_df.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
