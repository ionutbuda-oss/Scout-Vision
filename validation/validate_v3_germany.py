"""
ScoutVision V3 Alpha
Batch Validation
"""

from pathlib import Path

import pandas as pd

from engine.intelligence.v3.dna_engine_v3 import build_player_dna_v3
from engine.scoring.profile_models import ROLE_MODELS


RANKING_FILE = Path(
    "outputs/rankings/Germany_Regionalliga_U25_rankings.xlsx"
)

OUTPUT_DIR = Path("outputs/validation")

OUTPUT_FILE = OUTPUT_DIR / "v3_alpha_03_germany_regionalliga.csv"


SCORE_ALIASES = {
    "Distribution": (
        "Distribution Score",
        "Build-up Score",
    ),
    "Offensive Duels": (
        "Offensive Duels Score",
        "Duels Score",
    ),
}


def get_competencies(row, position_group):

    competencies = {}

    for competency_name in ROLE_MODELS[position_group]:

        candidates = SCORE_ALIASES.get(
            competency_name,
            (f"{competency_name} Score",),
        )

        score_column = next(
            (
                column
                for column in candidates
                if column in row.index
                and not pd.isna(row[column])
            ),
            None,
        )

        if score_column is None:
            raise RuntimeError(
                f"Missing competency score for "
                f"{competency_name}. Tried: {candidates}"
            )

        competencies[competency_name] = float(
            row[score_column]
        )

    return competencies


def evidence_score(confidence, name):

    for evidence in confidence.evidence:
        if evidence.name == name:
            return evidence.score

    raise RuntimeError(
        f"Evidence '{name}' not found."
    )


def main():

    df = pd.read_excel(RANKING_FILE)

    print("=" * 70)
    print("SCOUTVISION V3 ALPHA — BATCH VALIDATION")
    print("=" * 70)

    print(f"\nPlayers loaded: {len(df)}")

    results = []
    failures = []

    for _, row in df.iterrows():

        player = str(row.get("Player", "Unknown"))
        position_group = str(
            row.get("Position Group", "")
        ).strip()

        try:

            if position_group not in ROLE_MODELS:
                raise RuntimeError(
                    f"Unsupported position group: "
                    f"{position_group}"
                )

            competencies = get_competencies(
                row,
                position_group,
            )

            result = build_player_dna_v3(
                position_group,
                competencies,
            )

            confidence = result["confidence"]

            runner_up = result["runner_up_profile"]

            results.append({
                "Player": player,
                "Team": row.get("Team"),
                "Age": row.get("Age"),
                "Position Group": position_group,

                "Identity": (
                    result["primary_profile"].title
                ),

                "Runner Up": (
                    runner_up.title
                    if runner_up
                    else None
                ),

                "Primary Score": (
                    result["primary_score"]
                ),

                "Runner Up Score": (
                    result["runner_up_score"]
                ),

                "Gap": evidence_score(
                    confidence,
                    "Gap",
                ),

                "Dominance": evidence_score(
                    confidence,
                    "Dominance",
                ),

                "Distribution": evidence_score(
                    confidence,
                    "Distribution",
                ),

                "Confidence Raw": (
                    confidence.score
                ),

                "Confidence Level": (
                    confidence.level
                ),

                "Identity Type": (
                    result["identity_type"]
                ),

                "Versatility Score": (
                    result["versatility"]["score"]
                ),

                "Versatility Range": (
                    result["versatility"]["range"]
                ),

                "Versatility Dominance": (
                    result["versatility"]["dominance"]
                ),

                "Balanced": (
                    result["versatility"]["balanced"]
                ),

                "Completeness Level": (
                    result["completeness"].level
                ),

                "Completeness Minimum": (
                    result["completeness"].minimum
                ),

                "Completeness Range": (
                    result["completeness"].range
                ),

                "Complete Candidate": (
                    result["completeness"].is_complete_candidate
                ),
            })

        except Exception as exc:

            failures.append({
                "Player": player,
                "Position Group": position_group,
                "Error": str(exc),
            })

    results_df = pd.DataFrame(results)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"\nSuccessful: {len(results_df)}")
    print(f"Failures:   {len(failures)}")

    if failures:

        print("\nFAILURES")

        for failure in failures:
            print(
                failure["Player"],
                "|",
                failure["Position Group"],
                "|",
                failure["Error"],
            )

    if results_df.empty:
        raise RuntimeError(
            "No players were successfully evaluated."
        )

    print("\n" + "-" * 70)
    print("EVIDENCE DISTRIBUTIONS")
    print("-" * 70)

    columns = [
        "Gap",
        "Dominance",
        "Distribution",
        "Confidence Raw",
    ]

    summary = results_df[
        columns
    ].describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
        ]
    ).T

    print(
        summary[
            [
                "min",
                "25%",
                "50%",
                "mean",
                "75%",
                "90%",
                "95%",
                "max",
            ]
        ].round(2)
    )

    print("\n" + "-" * 70)
    print("IDENTITY TYPE DISTRIBUTION")
    print("-" * 70)

    print(
        results_df[
            "Identity Type"
        ].value_counts()
    )

    print("\n" + "-" * 70)
    print("CONFIDENCE LEVEL DISTRIBUTION")
    print("-" * 70)

    print(
        results_df[
            "Confidence Level"
        ].value_counts()
    )

    print("\n" + "-" * 70)
    print("CORRELATION — EVIDENCE COMPONENTS")
    print("-" * 70)

    print(
        results_df[
            [
                "Gap",
                "Dominance",
                "Distribution",
            ]
        ].corr().round(3)
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 70)
    print("BATCH VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
