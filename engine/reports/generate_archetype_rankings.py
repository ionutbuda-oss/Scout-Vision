"""
ScoutVision V3 - Archetype Rankings Generator

Creates recruitment boards by player archetype.
"""

from __future__ import annotations

import pandas as pd

from engine.config import Settings

from engine.reports.archetype_ranking import (
    ARCHETYPE_WEIGHTS,
    ARCHETYPE_POSITIONS,
    calculate_archetype_score,
)


SETTINGS = Settings()

INPUT_FILE = SETTINGS.rankings_file

OUTPUT_FILE = (
    SETTINGS.rankings_file.parent
    / f"{SETTINGS.competition_slug}_U25_archetype_rankings.xlsx"
)

MIN_MINUTES = 900
MIN_MATCHES = 10


def extract_metrics(row):

    metrics = {}

    for col in row.index:

        if col.endswith(" Score"):

            name = col.replace(" Score", "")

            if pd.notna(row[col]):

                metrics[name] = float(row[col])

    return metrics


def main():

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="All Ranked"
    )

    print("Players loaded:", len(df))


    archetype_results = {}


    for archetype in ARCHETYPE_WEIGHTS:

        results = []


        for _, row in df.iterrows():

            minutes = row.get("Minutes played", 0)
            matches = row.get("Matches played", 0)

            if pd.isna(minutes):
                minutes = 0

            if pd.isna(matches):
                matches = 0

            if minutes < MIN_MINUTES:
                continue

            if matches < MIN_MATCHES:
                continue


            allowed_positions = ARCHETYPE_POSITIONS.get(archetype)

            if allowed_positions:
                if row["Position Group"] not in allowed_positions:
                    continue

            metrics = extract_metrics(row)


            score = calculate_archetype_score(
                metrics,
                archetype
            )


            results.append(
                {
                    "Player": row.get("Player", ""),
                    "Team": row.get("Team", ""),
                    "Position": row.get("Position Group", ""),
                    "Archetype": archetype,
                    "Archetype Score": score,
                    "Scout Score": row.get("Scout Score", ""),
                    "Recruitment Score": row.get("Recruitment Score", ""),
                }
            )


        result_df = pd.DataFrame(results)

        if result_df.empty:
            continue

        result_df = result_df[
            result_df["Archetype Score"] > 0
        ]


        result_df = result_df.sort_values(
            "Archetype Score",
            ascending=False
        )


        result_df.insert(
            0,
            "Rank",
            range(1, len(result_df)+1)
        )


        archetype_results[archetype] = result_df


    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        for name, table in archetype_results.items():

            sheet = name[:31]

            table.to_excel(
                writer,
                sheet_name=sheet,
                index=False
            )


    print()
    print("✅ Archetype rankings generated")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
