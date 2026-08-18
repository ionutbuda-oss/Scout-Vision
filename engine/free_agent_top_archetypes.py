from pathlib import Path
import pandas as pd

from engine.reports.archetype_ranking import (
    ARCHETYPE_WEIGHTS,
    ARCHETYPE_POSITIONS,
    calculate_archetype_score,
)


INPUT_FILE = Path(
    "outputs/free_agents/free_agents_scoutvision_rankings.xlsx"
)

PRIORITY_FILE = Path(
    "outputs/free_agents/free_agent_verification_priority_v2.xlsx"
)

OUTPUT_FILE = Path(
    "outputs/free_agents/free_agent_top_archetypes.xlsx"
)

TOP_ARCHETYPES = 3


def extract_metrics(row):
    metrics = {}

    for col in row.index:

        if not str(col).endswith(" Score"):
            continue

        # Exclude global scores
        if col in {
            "Scout Score",
            "Performance Score",
            "Age Potential Score",
            "Recruitment Score",
        }:
            continue

        value = row[col]

        if pd.notna(value):
            metrics[
                str(col).replace(" Score", "")
            ] = float(value)

    return metrics


def calculate_player_archetypes(row):

    position = str(
        row.get("Position Group", "")
    ).strip()

    metrics = extract_metrics(row)

    results = []

    for archetype in ARCHETYPE_WEIGHTS:

        allowed_positions = ARCHETYPE_POSITIONS.get(
            archetype
        )

        if allowed_positions:

            if position not in allowed_positions:
                continue

        score = calculate_archetype_score(
            metrics,
            archetype,
        )

        if score <= 0:
            continue

        results.append(
            {
                "Archetype": archetype,
                "Archetype Score": score,
            }
        )

    return sorted(
        results,
        key=lambda x: x["Archetype Score"],
        reverse=True,
    )[:TOP_ARCHETYPES]


def main():

    priority = pd.read_excel(
        PRIORITY_FILE,
        sheet_name="Top 30 Verify V2",
    )

    source = pd.read_excel(
        INPUT_FILE
    )

    print("=" * 100)
    print("SCOUTVISION — FREE AGENT TOP 3 ARCHETYPES")
    print("=" * 100)

    output_rows = []

    for _, candidate in priority.iterrows():

        player_name = str(
            candidate["Player"]
        ).strip()

        matches = source[
            source["Player"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == player_name.casefold()
        ]

        if matches.empty:
            print(
                f"⚠ Player not found: {player_name}"
            )
            continue

        row = matches.iloc[0]

        archetypes = calculate_player_archetypes(
            row
        )

        result = {
            "Verification Rank": candidate[
                "Verification Rank"
            ],
            "League": candidate["League"],
            "Player": candidate["Player"],
            "Team": candidate["Team"],
            "Age": candidate["Age"],
            "Position Group": candidate[
                "Position Group"
            ],
            "Scout Score": candidate[
                "Scout Score"
            ],
            "Performance Score": candidate[
                "Performance Score"
            ],
            "Verification Priority Score": candidate[
                "Verification Priority Score"
            ],
            "Verification Priority": candidate[
                "Verification Priority"
            ],
            "Contract Status": candidate[
                "Contract Status"
            ],
        }

        for i in range(TOP_ARCHETYPES):

            if i < len(archetypes):

                result[
                    f"Archetype {i+1}"
                ] = archetypes[i]["Archetype"]

                result[
                    f"Archetype {i+1} Score"
                ] = archetypes[i]["Archetype Score"]

            else:

                result[
                    f"Archetype {i+1}"
                ] = ""

                result[
                    f"Archetype {i+1} Score"
                ] = ""

        output_rows.append(result)

    result_df = pd.DataFrame(
        output_rows
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        result_df.to_excel(
            writer,
            sheet_name="Top 30 Archetypes",
            index=False,
        )

    print()

    for _, row in result_df.iterrows():

        print(
            f'{int(row["Verification Rank"]):>2}. '
            f'{row["Player"]:<24} '
            f'{row["Position Group"]:<7} '
            f'Scout {row["Scout Score"]:>5}'
        )

        for i in range(1, 4):

            archetype = row[
                f"Archetype {i}"
            ]

            score = row[
                f"Archetype {i} Score"
            ]

            if pd.notna(archetype) and archetype:

                print(
                    f'    {i}. '
                    f'{archetype:<30} '
                    f'{score}'
                )

        print()

    print("=" * 100)
    print("✅ TOP 3 ARCHETYPES GENERATED")
    print("=" * 100)
    print(
        "Players analysed:",
        len(result_df)
    )
    print(
        "Output:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
