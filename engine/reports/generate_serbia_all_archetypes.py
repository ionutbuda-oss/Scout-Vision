"""
ScoutVision V3 - Serbia 1 ALL PLAYERS Archetype Rankings
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine.reports.archetype_ranking import (
    ARCHETYPE_WEIGHTS,
    ARCHETYPE_POSITIONS,
    calculate_archetype_score,
)


INPUT_FILE = Path(
    "outputs/rankings/Serbia_1_ALL_rankings.xlsx"
)

OUTPUT_FILE = Path(
    "outputs/rankings/Serbia_1_ALL_archetype_rankings.xlsx"
)

MIN_MINUTES = 900
MIN_MATCHES = 10
TOP_N = 5


def extract_metrics(row: pd.Series) -> dict[str, float]:
    metrics = {}

    for column in row.index:
        if column.endswith(" Score"):
            name = column.replace(" Score", "")

            if pd.notna(row[column]):
                metrics[name] = float(row[column])

    return metrics


def main() -> None:

    print("=" * 80)
    print("SCOUTVISION V3 — SERBIA 1 ALL PLAYERS ARCHETYPE RANKINGS")
    print("=" * 80)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_excel(
        INPUT_FILE,
        sheet_name="All Ranked",
    )

    print(f"Players loaded: {len(df)}")

    archetype_results = {}

    for archetype in ARCHETYPE_WEIGHTS:

        results = []

        allowed_positions = ARCHETYPE_POSITIONS.get(
            archetype
        )

        for _, row in df.iterrows():

            minutes = pd.to_numeric(
                row.get("Minutes played", 0),
                errors="coerce",
            )

            matches = pd.to_numeric(
                row.get("Matches played", 0),
                errors="coerce",
            )

            if pd.isna(minutes):
                minutes = 0

            if pd.isna(matches):
                matches = 0

            if minutes < MIN_MINUTES:
                continue

            if matches < MIN_MATCHES:
                continue

            position_group = row.get(
                "Position Group",
                "",
            )

            if allowed_positions:
                if position_group not in allowed_positions:
                    continue

            metrics = extract_metrics(row)

            score = calculate_archetype_score(
                metrics,
                archetype,
            )

            if score <= 0:
                continue

            results.append(
                {
                    "Player": row.get("Player", ""),
                    "Team": row.get("Team", ""),
                    "Position": position_group,
                    "Age": row.get("Age", ""),
                    "Minutes played": minutes,
                    "Matches played": matches,
                    "Archetype": archetype,
                    "Archetype Score": score,
                    "Scout Score": row.get(
                        "Scout Score",
                        "",
                    ),
                    "Performance Score": row.get(
                        "Performance Score",
                        "",
                    ),
                    "Recommendation": row.get(
                        "Recommendation",
                        "",
                    ),
                }
            )

        result_df = pd.DataFrame(results)

        if result_df.empty:
            continue

        result_df = result_df.sort_values(
            by="Archetype Score",
            ascending=False,
        ).reset_index(drop=True)

        result_df.insert(
            0,
            "Rank",
            range(1, len(result_df) + 1),
        )

        archetype_results[archetype] = result_df

        print(
            f"{archetype:<30} "
            f"{len(result_df):>3} eligible"
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        # Full rankings for every archetype
        for archetype, table in archetype_results.items():

            sheet = archetype[:31]

            table.to_excel(
                writer,
                sheet_name=sheet,
                index=False,
            )

        # One consolidated Top 5 table
        top5_rows = []

        for archetype, table in archetype_results.items():

            top5 = table.head(TOP_N)

            for _, row in top5.iterrows():

                top5_rows.append(
                    {
                        "Archetype": archetype,
                        "Rank": row["Rank"],
                        "Player": row["Player"],
                        "Team": row["Team"],
                        "Position": row["Position"],
                        "Age": row["Age"],
                        "Archetype Score": row[
                            "Archetype Score"
                        ],
                        "Scout Score": row[
                            "Scout Score"
                        ],
                        "Performance Score": row[
                            "Performance Score"
                        ],
                        "Recommendation": row[
                            "Recommendation"
                        ],
                    }
                )

        top5_df = pd.DataFrame(top5_rows)

        top5_df.to_excel(
            writer,
            sheet_name="TOP 5 ALL ARCHETYPES",
            index=False,
        )

    print()
    print("=" * 80)
    print("✅ SERBIA 1 ALL-PLAYER ARCHETYPE RANKINGS GENERATED")
    print("=" * 80)
    print(f"Output: {OUTPUT_FILE}")
    print(
        f"Archetypes generated: "
        f"{len(archetype_results)}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
