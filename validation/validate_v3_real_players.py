"""
ScoutVision V3 Alpha
Real Player Validation
"""

import pandas as pd

from engine.intelligence.v3.dna_engine_v3 import build_player_dna_v3
from engine.scoring.profile_models import ROLE_MODELS


RANKING_FILE = "outputs/rankings/France_National_U25_rankings.xlsx"


def main():

    df = pd.read_excel(RANKING_FILE)

    print("=" * 70)
    print("SCOUTVISION V3 ALPHA — REAL PLAYER VALIDATION")
    print("=" * 70)

    print(f"\nPlayers loaded: {len(df)}")

    # Prefer a striker for the first real-player test.
    candidates = df[
        df["Position Group"].astype(str) == "ST"
    ]

    if candidates.empty:
        raise RuntimeError("No ST players found in ranking file.")

    # Ranking workbook should already be ordered,
    # so take the first available striker.
    row = candidates.iloc[0]

    position_group = str(row["Position Group"]).strip()

    competencies = {}

    for competency_name in ROLE_MODELS[position_group]:

        column = f"{competency_name} Score"

        # Compatibility with known historical aliases.
        if competency_name == "Distribution":
            alternatives = [
                "Distribution Score",
                "Build-up Score",
            ]
        elif competency_name == "Offensive Duels":
            alternatives = [
                "Offensive Duels Score",
                "Duels Score",
            ]
        else:
            alternatives = [column]

        score_column = next(
            (
                candidate
                for candidate in alternatives
                if candidate in row.index
                and not pd.isna(row[candidate])
            ),
            None,
        )

        if score_column is None:
            raise RuntimeError(
                f"Missing competency score for {competency_name}. "
                f"Tried: {alternatives}"
            )

        competencies[competency_name] = float(
            row[score_column]
        )

    print("\nREAL PLAYER")
    print("Player:", row["Player"])
    print("Team:", row["Team"])
    print("Position:", row["Position"])
    print("Position Group:", position_group)

    print("\nCOMPETENCIES")

    for name, score in competencies.items():
        print(f"{name:<25} {score:.2f}")

    result = build_player_dna_v3(
        position_group,
        competencies,
    )

    print("\n" + "-" * 70)
    print("V3 DECISION")
    print("-" * 70)

    print(
        "Identity:",
        result["primary_profile"].title,
    )

    print(
        "Identity Type:",
        result["identity_type"],
    )

    print(
        "Primary Score:",
        result["primary_score"],
    )

    runner_up = result["runner_up_profile"]

    print(
        "Runner-up:",
        runner_up.title if runner_up else None,
    )

    print(
        "Runner-up Score:",
        result["runner_up_score"],
    )

    print(
        "Difference:",
        result["difference"],
    )

    confidence = result["confidence"]

    print("\nCONFIDENCE")

    print("Score:", confidence.score)
    print("Level:", confidence.level)

    print("\nEVIDENCE")

    for evidence in confidence.evidence:
        print(
            f"{evidence.name:<15}"
            f"{evidence.score:>8.2f}   "
            f"{evidence.explanation}"
        )

    print("\nVERSATILITY")

    for key, value in result["versatility"].items():
        print(f"{key:<15} {value}")

    print("\nCOMPLETENESS")

    completeness = result["completeness"]

    print(f"{'level':<15} {completeness.level}")
    print(f"{'minimum':<15} {completeness.minimum}")
    print(f"{'range':<15} {completeness.range}")
    print(
        f"{'complete':<15} "
        f"{completeness.is_complete_candidate}"
    )

    print("\nDECISION TRACE")

    for step in result["trace"]:
        print(step)

    print("\n" + "=" * 70)
    print("REAL PLAYER VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
