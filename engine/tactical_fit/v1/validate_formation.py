"""Cross-league validation for ScoutVision Tactical Fit V1."""

from __future__ import annotations

import argparse

import pandas as pd

from engine.tactical_fit.v1.fit_engine import evaluate_position_fit
from engine.tactical_fit.v1.role_library import ROLE_LIBRARY


LEAGUES = {
    "Belgium Challenger Pro League":
        "outputs/rankings/Belgium_Challenger_Pro_League_U25_rankings.xlsx",
    "France National":
        "outputs/rankings/France_National_U25_rankings.xlsx",
    "Germany Regionalliga":
        "outputs/rankings/Germany_Regionalliga_U25_rankings.xlsx",
}


def score_column(competency: str) -> str:
    return f"{competency} Score"


def validate_position(
    position: str,
    formation: str = "4-3-3",
) -> pd.DataFrame:
    """Evaluate one position across all configured leagues."""

    if formation not in ROLE_LIBRARY:
        raise ValueError(
            f"Unknown formation {formation!r}. "
            f"Available: {', '.join(ROLE_LIBRARY)}"
        )

    if position not in ROLE_LIBRARY[formation]:
        raise ValueError(
            f"{position!r} is not configured for {formation}."
        )

    role_definitions = ROLE_LIBRARY[formation][position]

    required_competencies = sorted({
        competency
        for role in role_definitions.values()
        for competency in role["weights"]
    })

    records = []

    for league, path in LEAGUES.items():

        xls = pd.ExcelFile(path)

        if position not in xls.sheet_names:
            raise RuntimeError(
                f"{league}: sheet {position!r} missing"
            )

        df = pd.read_excel(path, sheet_name=position)

        required_columns = [
            score_column(name)
            for name in required_competencies
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise RuntimeError(
                f"{league} / {position}: "
                f"missing competency columns {missing}"
            )

        for _, player in df.iterrows():

            competencies = {
                name: float(player[score_column(name)])
                for name in required_competencies
            }

            results = evaluate_position_fit(
                formation=formation,
                position_group=position,
                competencies=competencies,
            )

            best = results[0]
            second = results[1] if len(results) > 1 else results[0]

            record = {
                "League": league,
                "Position": position,
                "Player": player["Player"],
                "Team": player["Team"],
                "Age": player["Age"],
                "Scout Score": player["Scout Score"],
                "Best Fit": best["role"],
                "Best Fit Score": best["fit_score"],
                "Secondary Fit": second["role"],
                "Secondary Fit Score": second["fit_score"],
                "Fit Gap": round(
                    best["fit_score"] - second["fit_score"],
                    1,
                ),
            }

            for result in results:
                record[result["role"]] = result["fit_score"]

            records.append(record)

    return pd.DataFrame(records)


def print_position_report(
    position: str,
    data: pd.DataFrame,
    formation: str,
) -> None:
    """Print validation diagnostics for one position."""

    role_titles = [
        role["title"]
        for role in ROLE_LIBRARY[formation][position].values()
    ]

    print("\n")
    print("=" * 100)
    print(f"{formation} — {position} CROSS-LEAGUE VALIDATION")
    print("=" * 100)

    print("\nPOPULATION")
    print("-" * 60)

    population = data.groupby("League").size()

    for league, count in population.items():
        print(f"{league:<42} {count:>4}")

    print(f"{'TOTAL':<42} {len(data):>4}")

    print("\nBEST FIT DISTRIBUTION")
    print("-" * 80)

    distribution = pd.crosstab(
        data["League"],
        data["Best Fit"],
    )

    print(distribution.to_string())

    print("\nBEST FIT DISTRIBUTION (%)")
    print("-" * 80)

    distribution_pct = (
        pd.crosstab(
            data["League"],
            data["Best Fit"],
            normalize="index",
        )
        .mul(100)
        .round(1)
    )

    print(distribution_pct.to_string())

    print("\nMEAN ROLE FIT BY LEAGUE")
    print("-" * 80)

    means = (
        data.groupby("League")[role_titles]
        .mean()
        .round(1)
    )

    print(means.to_string())

    print("\nFIT GAP BY LEAGUE")
    print("-" * 80)

    gaps = (
        data.groupby("League")["Fit Gap"]
        .agg([
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max",
        ])
        .round(1)
    )

    print(gaps.to_string())

    print("\nOVERALL BEST FIT DISTRIBUTION")
    print("-" * 60)

    overall = (
        data["Best Fit"]
        .value_counts()
        .reindex(role_titles, fill_value=0)
    )

    overall_pct = (
        overall
        .div(len(data))
        .mul(100)
        .round(1)
    )

    for role in role_titles:
        count = int(overall[role])

        marker = "  <-- DEAD ROLE" if count == 0 else ""

        print(
            f"{role:<30} "
            f"{count:>4} "
            f"({overall_pct[role]:>5.1f}%){marker}"
        )

    print("\nROLE LEADERS")
    print("-" * 100)

    for role in role_titles:

        leader = data.sort_values(
            role,
            ascending=False,
        ).iloc[0]

        print(
            f"{role:<30} "
            f"{str(leader['Player']):<24} "
            f"{leader[role]:>5.1f}   "
            f"{leader['League']}"
        )


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="ScoutVision Tactical Fit cross-league validator."
    )

    parser.add_argument(
        "--formation",
        default="4-3-3",
        choices=list(ROLE_LIBRARY.keys()),
        help="Formation to validate.",
    )

    return parser.parse_args()


def main() -> None:

    args = parse_args()
    formation = args.formation
    positions = list(ROLE_LIBRARY[formation].keys())

    print("=" * 100)
    print(
        f"SCOUTVISION TACTICAL FIT V1 — "
        f"FULL {formation} VALIDATION"
    )
    print("=" * 100)

    print("\nPOSITIONS")
    print(", ".join(positions))

    all_results = []

    for position in positions:

        data = validate_position(
            position,
            formation=formation,
        )

        all_results.append(data)

        print_position_report(
            position,
            data,
            formation,
        )

    combined = pd.concat(
        all_results,
        ignore_index=True,
    )

    print("\n")
    print("=" * 100)
    print("FULL FORMATION SUMMARY")
    print("=" * 100)

    population = pd.crosstab(
        combined["League"],
        combined["Position"],
    )

    print("\nPLAYER POPULATION")
    print(population.to_string())

    print("\nTOTAL EVALUATIONS")
    print(len(combined))

    print("\nMEAN BEST FIT BY POSITION")
    print(
        combined.groupby("Position")["Best Fit Score"]
        .mean()
        .round(1)
        .to_string()
    )

    print("\nMEAN FIT GAP BY POSITION")
    print(
        combined.groupby("Position")["Fit Gap"]
        .mean()
        .round(1)
        .to_string()
    )

    print("\n" + "=" * 100)
    print("VALIDATION COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()
