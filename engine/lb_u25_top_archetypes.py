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

OUTPUT_FILE = Path(
    "outputs/free_agents/lb_u25_top_archetypes.xlsx"
)

TARGET_PLAYERS = [
    "V. Durdevic",
    "M. Riznič",
    "L. Penxa",
    "David Moreira",
    "F. Slavicek",
    "Lucas Alcázar",
    "N. Krsmanović",
    "André Lopes",
    "M. Šubert",
]

def extract_metrics(row):
    metrics = {}

    for col in row.index:
        if not str(col).endswith(" Score"):
            continue

        if col in {
            "Scout Score",
            "Performance Score",
            "Age Potential Score",
            "Recruitment Score",
        }:
            continue

        if pd.notna(row[col]):
            metrics[
                str(col).replace(" Score", "")
            ] = float(row[col])

    return metrics


def top_archetypes(row):

    position = str(
        row["Position Group"]
    ).strip()

    metrics = extract_metrics(row)

    results = []

    for archetype in ARCHETYPE_WEIGHTS:

        allowed = ARCHETYPE_POSITIONS.get(
            archetype
        )

        if allowed and position not in allowed:
            continue

        score = calculate_archetype_score(
            metrics,
            archetype,
        )

        if score > 0:
            results.append(
                (
                    archetype,
                    score,
                )
            )

    return sorted(
        results,
        key=lambda x: x[1],
        reverse=True,
    )[:3]


def main():

    df = pd.read_excel(
        INPUT_FILE
    )

    target = df[
        df["Player"]
        .astype(str)
        .str.strip()
        .isin(TARGET_PLAYERS)
    ].copy()

    target = target[
        pd.to_numeric(
            target["Age"],
            errors="coerce"
        ) < 25
    ]

    output = []

    print("=" * 100)
    print("SCOUTVISION — U25 LEFT-BACK SEARCH")
    print("=" * 100)

    for _, row in target.iterrows():

        archetypes = top_archetypes(row)

        result = {
            "Player": row["Player"],
            "Team": row["Team"],
            "Age": row["Age"],
            "Position": row["Position"],
            "Position Group": row["Position Group"],
            "Matches played": row["Matches played"],
            "Minutes played": row["Minutes played"],
            "Scout Score": row["Scout Score"],
            "Performance Score": row["Performance Score"],
            "Recommendation": row["Recommendation"],
        }

        for i in range(3):

            if i < len(archetypes):
                result[
                    f"Archetype {i+1}"
                ] = archetypes[i][0]

                result[
                    f"Archetype {i+1} Score"
                ] = archetypes[i][1]
            else:
                result[
                    f"Archetype {i+1}"
                ] = ""

                result[
                    f"Archetype {i+1} Score"
                ] = ""

        output.append(result)

        print()
        print(
            f'{row["Player"]:<24} '
            f'{int(row["Age"])} ani | '
            f'{row["Position"]} | '
            f'Scout {row["Scout Score"]}'
        )

        for i, (name, score) in enumerate(
            archetypes,
            start=1
        ):
            print(
                f"   {i}. {name:<30} {score}"
            )

    result_df = pd.DataFrame(output)

    result_df = result_df.sort_values(
        "Scout Score",
        ascending=False,
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
            sheet_name="LB U25",
            index=False,
        )

    print()
    print("=" * 100)
    print("✅ U25 LB ARCHETYPE BOARD GENERATED")
    print("=" * 100)
    print(
        "Candidates analysed:",
        len(result_df)
    )
    print(
        "Output:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
